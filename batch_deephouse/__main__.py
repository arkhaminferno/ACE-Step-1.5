"""Allow: python -m batch_deephouse [--slug ...] | deliver | export-metadata | ae-batch."""

import sys


def main() -> int:
    """Dispatch generate CLI or subcommands."""
    if len(sys.argv) > 1 and sys.argv[1] == "deliver":
        from batch_deephouse.deliver import main as deliver_main

        return deliver_main(sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == "export-metadata":
        from batch_deephouse.publish_metadata import main as export_main

        return export_main()
    if len(sys.argv) > 1 and sys.argv[1] == "ae-batch":
        from batch_deephouse.ae_batch_cli import main as ae_main

        return ae_main(sys.argv[2:])
    from batch_deephouse.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
