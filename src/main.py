import argparse
from rich import print


def run_paper():
    print('[green]Paper mode started[/green]')
    print('TODO: wire market fetch + signal + risk + broker')


def run_backtest():
    print('[cyan]Backtest mode started[/cyan]')
    print('TODO: replay historical market snapshots')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['paper', 'backtest'], default='paper')
    args = parser.parse_args()

    if args.mode == 'paper':
        run_paper()
    else:
        run_backtest()


if __name__ == '__main__':
    main()
