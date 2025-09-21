#!/usr/bin/env python3
"""
OpenIDE Client CLI
Командная строка для OpenIDE Client
"""

import click
import json
import sys
from .client import create_client, create_api_client

@click.group()
@click.version_option(version="1.0.1")
def cli():
    """OpenIDE Client - Python библиотека для работы с OpenIDE"""
    pass

@cli.command()
@click.option('--host', default='127.0.0.1', help='OpenIDE API host')
@click.option('--port', default=5000, help='OpenIDE API port')
@click.option('--api-key', help='API key for authentication')
def health(host, port, api_key):
    """Проверить здоровье OpenIDE API"""
    try:
        client = create_api_client(host, port, api_key)
        result = client.health_check()
        click.echo(f"✅ OpenIDE API здоров: {result}")
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}")
        sys.exit(1)

@cli.command()
@click.option('--host', default='127.0.0.1', help='OpenIDE API host')
@click.option('--port', default=5000, help='OpenIDE API port')
@click.option('--api-key', help='API key for authentication')
def containers(host, port, api_key):
    """Список контейнеров"""
    try:
        client = create_api_client(host, port, api_key)
        result = client.list_containers()
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}")
        sys.exit(1)

@cli.command()
@click.option('--host', default='127.0.0.1', help='OpenIDE API host')
@click.option('--port', default=5000, help='OpenIDE API port')
@click.option('--api-key', help='API key for authentication')
@click.argument('image', default='python:3.12')
@click.argument('command', default='bash')
def create(host, port, api_key, image, command):
    """Создать контейнер"""
    try:
        client = create_api_client(host, port, api_key)
        result = client.create_container(image, command)
        click.echo(f"✅ Контейнер создан: {result['container_id']}")
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}")
        sys.exit(1)

@cli.command()
@click.option('--host', default='127.0.0.1', help='OpenIDE API host')
@click.option('--port', default=5000, help='OpenIDE API port')
@click.option('--api-key', help='API key for authentication')
@click.argument('container_id')
@click.argument('command')
def exec(host, port, api_key, container_id, command):
    """Выполнить команду в контейнере"""
    try:
        client = create_api_client(host, port, api_key)
        result = client.exec_command(container_id, command)
        click.echo(result['output'])
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}")
        sys.exit(1)

@cli.command()
@click.option('--host', default='127.0.0.1', help='OpenIDE API host')
@click.option('--port', default=5000, help='OpenIDE API port')
@click.option('--api-key', help='API key for authentication')
@click.argument('container_id')
def delete(host, port, api_key, container_id):
    """Удалить контейнер"""
    try:
        client = create_api_client(host, port, api_key)
        result = client.delete_container(container_id)
        if result.get('success'):
            click.echo(f"✅ Контейнер {container_id} удален")
        else:
            click.echo(f"❌ Не удалось удалить контейнер {container_id}")
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli()
