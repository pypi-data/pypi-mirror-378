import argparse
import json
import logging
import signal
import sys
from logging.handlers import RotatingFileHandler
from math import ceil
from pathlib import Path
from typing import List

import trio
from fastly_bouncer.config import (
    Config,
    ConfigGenerator,
    FastlyAccountConfig,
    FastlyServiceConfig,
    parse_config_file,
    print_config,
)
from fastly_bouncer.fastly_api import ACL_CAPACITY, FastlyAPI
from fastly_bouncer.service import ACLCollection, Service
from fastly_bouncer.utils import (
    SUPPORTED_ACTIONS,
    VERSION,
    CustomFormatter,
    get_default_logger,
    with_suffix,
)
from pycrowdsec.client import StreamClient

logger: logging.Logger = get_default_logger()

exiting = False


def sigterm_signal_handler(signum, frame):
    global exiting
    exiting = True
    logger.info("exiting")


signal.signal(signal.SIGTERM, sigterm_signal_handler)
signal.signal(signal.SIGINT, sigterm_signal_handler)


async def setup_action_for_service(
    fastly_api: FastlyAPI,
    action: str,
    service_cfg: FastlyServiceConfig,
    service_version,
    fast_creation: bool = False,
) -> ACLCollection:

    acl_count = ceil(service_cfg.max_items / ACL_CAPACITY)
    acl_collection = ACLCollection(
        api=fastly_api,
        service_id=service_cfg.id,
        version=service_version,
        action=action,
        max_items=service_cfg.max_items,
        state=set(),
        fast_creation=fast_creation,
    )
    logger.info(
        with_suffix(
            f"creating acl collection of {acl_count} acls for {action} action",
            service_id=service_cfg.id,
        )
    )
    acls = await acl_collection.create_acls(acl_count)
    acl_collection.acls = acls
    logger.info(
        with_suffix(
            f"created acl collection for {action} action",
            service_id=service_cfg.id,
        )
    )
    return acl_collection


async def setup_service(
    service_cfg: FastlyServiceConfig,
    fastly_api: FastlyAPI,
    cleanup_mode: bool,
    sender_chan: trio.MemorySendChannel,
    fast_creation: bool = False,
):
    comment = None
    service_id = service_cfg.id
    if cleanup_mode:
        comment = "Clone cleaned from CrowdSec resources"

    # Use reference_version if provided, otherwise get the active version
    if service_cfg.reference_version:
        version_to_clone = service_cfg.reference_version
    else:
        version_to_clone = await fastly_api.get_version_to_clone(service_id)
    version = await fastly_api.clone_version_for_service_from_given_version(
        service_cfg.id, version_to_clone, comment
    )
    logger.info(
        with_suffix(
            f"new version {version} for service created",
            service_id=service_id,
        )
    )

    logger.info(
        with_suffix(
            "cleaning existing crowdsec resources (if any)",
            service_id=service_cfg.id,
            version=version,
        )
    )

    await fastly_api.clear_crowdsec_resources(service_cfg.id, version)
    if cleanup_mode:
        sender_chan.close()
        return

    logger.info(
        with_suffix(
            "cleaned existing crowdsec resources (if any)",
            service_id=service_cfg.id,
            version=version,
        )
    )

    acl_collection_by_action = {}
    for action in SUPPORTED_ACTIONS:
        acl_collection = await setup_action_for_service(
            fastly_api, action, service_cfg, version, fast_creation
        )
        acl_collection_by_action[action] = acl_collection
        # Small delay to ensure proper ordering at Fastly API level
        await trio.sleep(1)

    async with sender_chan:
        s = Service(
            api=fastly_api,
            recaptcha_secret=service_cfg.recaptcha_secret_key,
            recaptcha_site_key=service_cfg.recaptcha_site_key,
            acl_collection_by_action=acl_collection_by_action,
            service_id=service_cfg.id,
            version=version,
            activate=service_cfg.activate,
            captcha_expiry_duration=service_cfg.captcha_cookie_expiry_duration,
        )
        await s.create_static_vcls()
        await sender_chan.send(s)


async def setup_account(
    account_cfg: FastlyAccountConfig,
    cleanup: bool,
    sender_chan,
    fast_creation: bool = False,
):
    fastly_api = FastlyAPI(account_cfg.account_token)
    new_services = []
    sender, receiver = trio.open_memory_channel(0)
    async with trio.open_nursery() as n:
        async with sender:
            for cfg in account_cfg.services:
                n.start_soon(
                    setup_service,
                    cfg,
                    fastly_api,
                    cleanup,
                    sender.clone(),
                    fast_creation,
                )

        async with receiver:
            async for service in receiver:
                new_services.append(service)

    async with sender_chan:
        await sender_chan.send(new_services)


async def setup_fastly_infra(config: Config, cleanup_mode):
    p = Path(config.cache_path)
    if p.exists():
        logger.info("Cache file exists")
        async with await trio.open_file(config.cache_path) as f:
            s = await f.read()
            if not s:
                logger.warning(f"Cache file at {config.cache_path} is empty")
            else:
                cache = json.loads(s)
                services = list(
                    map(Service.from_jsonable_dict, cache["service_states"])
                )
                logger.info("Loaded existing infra using cache: ")
                for service in services:
                    logger.info(
                        f"service_id: {service.service_id}, version: {service.version}"
                    )
                if not cleanup_mode:
                    return services
    else:
        p.parent.mkdir(exist_ok=True, parents=True)

    if cleanup_mode:
        logger.info("Cleaning fastly infra")
    else:
        logger.info("Setting up fastly infra")

    services = []
    sender, receiver = trio.open_memory_channel(0)
    async with trio.open_nursery() as n:
        async with sender:
            for cfg in config.fastly_account_configs:
                n.start_soon(
                    setup_account,
                    cfg,
                    cleanup_mode,
                    sender.clone(),
                    config.acl_fast_creation,
                )

        async for service_chunk in receiver:
            services.extend(service_chunk)

    logger.info("Fastly infra setup complete")
    return services


def set_logger(config: Config):
    list(map(logger.removeHandler, logger.handlers))
    logger.setLevel(config.get_log_level())
    if config.log_mode == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    elif config.log_mode == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    elif config.log_mode == "file":
        handler = RotatingFileHandler(config.log_file, mode="a+")
    else:
        raise ValueError(f"unknown log mode {config.log_mode}")
    formatter = CustomFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info(f"Starting fastly-bouncer-v{VERSION}")


def buildClientParams(config: Config):
    # Build StreamClient parameters
    client_params = {
        "api_key": config.crowdsec_config.lapi_key,
        "lapi_url": config.crowdsec_config.lapi_url,
        "interval": config.update_frequency,
        "user_agent": f"fastly-bouncer/v{VERSION}",
        "scopes": ("ip", "range", "country", "as"),
    }
    # Origins to include decisions from
    if config.crowdsec_config.only_include_decisions_from:
        client_params["only_include_decisions_from"] = tuple(
            config.crowdsec_config.only_include_decisions_from
        )

    # Include/exclude scenarios
    if config.crowdsec_config.include_scenarios_containing:
        client_params["include_scenarios_containing"] = tuple(
            config.crowdsec_config.include_scenarios_containing
        )

    if config.crowdsec_config.exclude_scenarios_containing:
        client_params["exclude_scenarios_containing"] = tuple(
            config.crowdsec_config.exclude_scenarios_containing
        )

    # SSL/TLS options
    if config.crowdsec_config.insecure_skip_verify:
        client_params["insecure_skip_verify"] = True

    if config.crowdsec_config.key_path:
        client_params["key_path"] = config.crowdsec_config.key_path

    if config.crowdsec_config.cert_path:
        client_params["cert_path"] = config.crowdsec_config.cert_path

    if config.crowdsec_config.ca_cert_path:
        client_params["ca_cert_path"] = config.crowdsec_config.ca_cert_path

    return client_params


async def run(config: Config, services: List[Service]):
    # Build StreamClient parameters
    client_params = buildClientParams(config)

    crowdsec_client = StreamClient(**client_params)
    crowdsec_client.run()
    await trio.sleep(
        2
    )  # Wait for initial polling by bouncer, so we start with a hydrated state
    if not crowdsec_client.is_running():
        return
    previous_states = {}
    while True and not exiting:
        logger.debug(
            f"Retrieving decisions from LAPI with scopes {client_params['scopes']} "
            f"and origins {client_params['only_include_decisions_from']} "
            f"and include_scenarios_containing {client_params.get('include_scenarios_containing', [])} "
            f"and exclude_scenarios_containing {client_params.get('exclude_scenarios_containing', [])}"
        )
        new_state = crowdsec_client.get_current_decisions()
        logger.info(f"Retrieved {len(new_state)} active decisions from LAPI")

        async with trio.open_nursery() as n:
            for s in services:
                n.start_soon(s.transform_state, new_state)

        new_states = list(map(lambda service: service.as_jsonable_dict(), services))
        if new_states != previous_states:
            logger.debug("Updating local cache file")
            new_cache = {"service_states": new_states, "bouncer_version": VERSION}
            async with await trio.open_file(config.cache_path, "w") as f:
                await f.write(json.dumps(new_cache, indent=4))
            logger.info("Local cache updated")
            previous_states = new_states

        if exiting:
            return

        await trio.sleep(config.update_frequency)


async def start(config: Config, cleanup_mode):
    global services
    services = await setup_fastly_infra(config, cleanup_mode)
    if cleanup_mode:
        if Path(config.cache_path).exists():
            logger.info("Cleaning cache")
            with open(config.cache_path, "w") as _:
                pass
        return

    await run(config, services)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-c", type=Path, help="Path to configuration file.")
    arg_parser.add_argument(
        "-d", help="Whether to cleanup resources.", action="store_true"
    )
    arg_parser.add_argument(
        "-e",
        help="Edit existing config with new tokens (requires both -g and -c).",
        action="store_true",
    )
    arg_parser.add_argument(
        "-g", type=str, help="Comma separated tokens to generate config for."
    )
    arg_parser.add_argument(
        "-o", type=str, help="Path to file to output the generated config."
    )
    arg_parser.add_help = True
    args = arg_parser.parse_args()
    # Validate edit mode requirements
    if args.e:
        if not args.g:
            print("Edit mode (-e) requires tokens (-g)", file=sys.stderr)
            arg_parser.print_help()
            sys.exit(1)
        if not args.c:
            print("Edit mode (-e) requires config file (-c)", file=sys.stderr)
            arg_parser.print_help()
            sys.exit(1)
        if args.o:
            print(
                "Edit mode (-e) cannot be used with output file (-o)", file=sys.stderr
            )
            arg_parser.print_help()
            sys.exit(1)

    # Handle config generation
    if args.g and not args.e:
        gc = trio.run(ConfigGenerator().generate_config, args.g)
        print_config(gc, args.o)
        sys.exit(0)

    # Handle config editing
    if args.e:
        if not args.c.exists():
            print(f"Config at {args.c} doesn't exist", file=sys.stderr)
            sys.exit(1)
        try:
            existing_config = parse_config_file(args.c)
            edited_config = trio.run(
                ConfigGenerator().edit_config, args.g, existing_config
            )

            # Write the edited config back to the original file
            with open(args.c, "w") as f:
                f.write(edited_config)

            print(f"Config successfully updated: {args.c}")
            sys.exit(0)
        except Exception as e:
            print(f"Got error {e} while editing config at {args.c}", file=sys.stderr)
            sys.exit(1)

    # Handle normal run
    if not args.g:
        if not args.c:
            print("Config file not provided", file=sys.stderr)
            arg_parser.print_help()
            sys.exit(1)
        else:
            if not args.c.exists():
                print(f"Config at {args.c} doesn't exist", file=sys.stderr)
                sys.exit(1)
            else:
                try:
                    config = parse_config_file(args.c)
                    set_logger(config)
                    logger.info("Parsed config successfully")
                    trio.run(start, config, args.d)
                except Exception as e:
                    logger.error(f"Got error {e} while parsing config at {args.c}")
                    sys.exit(1)


if __name__ == "__main__":
    main()
