#!/usr/bin/env python3
"""
OpenIDE Client CLI
Консольный интерфейс для OpenIDE Client
"""

import click
import json
import sys
from .client import create_client, create_api_client

@click.group()
@click.version_option(version="1.0.2")
def cli():
    """OpenIDE Client - Python библиотека для работы с OpenIDE"""
    pass

@cli.command()
@click.option('--openide-dir', '-d', help='Путь к директории OpenIDE')
@click.option('--timeout', '-t', default=30, help='Таймаут операций в секундах')
@click.option('--api-key', '-k', help='API ключ для аутентификации')
def info(openide_dir, timeout, api_key):
    """Информация о OpenIDE"""
    try:
        client = create_client(openide_dir, timeout, api_key)
        info = client.system_info()
        click.echo(json.dumps(info, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Ошибка: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--openide-dir', '-d', help='Путь к директории OpenIDE')
@click.option('--timeout', '-t', default=30, help='Таймаут операций в секундах')
@click.option('--api-key', '-k', help='API ключ для аутентификации')
def containers(openide_dir, timeout, api_key):
    """Список контейнеров"""
    try:
        client = create_client(openide_dir, timeout, api_key)
        containers = client.list_containers()
        click.echo(json.dumps(containers, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Ошибка: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('image')
@click.argument('command')
@click.option('--openide-dir', '-d', help='Путь к директории OpenIDE')
@click.option('--timeout', '-t', default=30, help='Таймаут операций в секундах')
@click.option('--api-key', '-k', help='API ключ для аутентификации')
@click.option('--detach/--no-detach', default=True, help='Запустить в фоне')
def run(image, command, openide_dir, timeout, api_key, detach):
    """Запустить контейнер"""
    try:
        client = create_client(openide_dir, timeout, api_key)
        result = client.run_container(image, command, detach=detach)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Ошибка: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('container_id')
@click.argument('command')
@click.option('--openide-dir', '-d', help='Путь к директории OpenIDE')
@click.option('--timeout', '-t', default=30, help='Таймаут операций в секундах')
@click.option('--api-key', '-k', help='API ключ для аутентификации')
def exec(container_id, command, openide_dir, timeout, api_key):
    """Выполнить команду в контейнере"""
    try:
        client = create_client(openide_dir, timeout, api_key)
        result = client.exec_command(container_id, command)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Ошибка: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('container_id')
@click.option('--openide-dir', '-d', help='Путь к директории OpenIDE')
@click.option('--timeout', '-t', default=30, help='Таймаут операций в секундах')
@click.option('--api-key', '-k', help='API ключ для аутентификации')
def stop(container_id, openide_dir, timeout, api_key):
    """Остановить контейнер"""
    try:
        client = create_client(openide_dir, timeout, api_key)
        result = client.stop_container(container_id)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Ошибка: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('container_id')
@click.option('--openide-dir', '-d', help='Путь к директории OpenIDE')
@click.option('--timeout', '-t', default=30, help='Таймаут операций в секундах')
@click.option('--api-key', '-k', help='API ключ для аутентификации')
def remove(container_id, openide_dir, timeout, api_key):
    """Удалить контейнер"""
    try:
        client = create_client(openide_dir, timeout, api_key)
        result = client.remove_container(container_id)
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Ошибка: {e}", err=True)
        sys.exit(1)

def main():
    """Главная функция CLI"""
    cli()

if __name__ == '__main__':
    main()
