#!/usr/bin/env python3
"""
Docker build script for User Management Flask Server

This script provides convenient commands for building and managing
Docker images and containers.
"""

import subprocess
import sys
import argparse
import os

def run_command(command, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        sys.exit(1)

def build_image(tag="user-management-server", dockerfile="docker/Dockerfile"):
    """Build Docker image."""
    print(f"Building Docker image: {tag}")
    command = f"docker build -t {tag} -f {dockerfile} ."
    run_command(command)
    print(f"✅ Successfully built image: {tag}")

def run_container(tag="user-management-server", port=5000, name="flask-server", detached=False):
    """Run Docker container."""
    print(f"Running Docker container: {name}")
    
    # Stop existing container if it exists
    run_command(f"docker stop {name}", check=False)
    run_command(f"docker rm {name}", check=False)
    
    # Create data directory if it doesn't exist
    os.makedirs("./data", exist_ok=True)
    
    detach_flag = "-d" if detached else ""
    command = f"docker run {detach_flag} -p {port}:5000 --name {name} -v $(pwd)/data:/app/data {tag}"
    
    run_command(command)
    
    if detached:
        print(f"✅ Container {name} is running in background on port {port}")
        print(f"   Health check: curl http://localhost:{port}/health")
        print(f"   View logs: docker logs {name}")
        print(f"   Stop container: docker stop {name}")
    else:
        print(f"✅ Container {name} started on port {port}")

def compose_up(detached=False, build=False, env="prod"):
    """Run docker-compose up."""
    print(f"Starting services with docker-compose ({env} environment)")
    
    flags = []
    if detached:
        flags.append("-d")
    if build:
        flags.append("--build")
    
    compose_file = f"docker/docker-compose.{env}.yml"
    command = f"docker-compose -f {compose_file} up {' '.join(flags)}"
    run_command(command)
    
    if detached:
        print("✅ Services started in background")
        print(f"   View logs: docker-compose -f {compose_file} logs -f")
        print(f"   Stop services: docker-compose -f {compose_file} down")

def compose_down(env="prod"):
    """Run docker-compose down."""
    print(f"Stopping services with docker-compose ({env} environment)")
    compose_file = f"docker/docker-compose.{env}.yml"
    run_command(f"docker-compose -f {compose_file} down")
    print("✅ Services stopped")

def show_status():
    """Show Docker container status."""
    print("Docker container status:")
    run_command("docker ps -a --filter name=flask-server")
    
    print("\nDocker images:")
    run_command("docker images --filter reference=user-management-server")

def cleanup():
    """Clean up Docker resources."""
    print("Cleaning up Docker resources...")
    
    # Stop and remove containers
    run_command("docker stop flask-server", check=False)
    run_command("docker rm flask-server", check=False)
    
    # Remove images
    run_command("docker rmi user-management-server", check=False)
    
    # Clean up compose resources
    run_command("docker-compose -f docker/docker-compose.prod.yml down --rmi all --volumes", check=False)
    run_command("docker-compose -f docker/docker-compose.dev.yml down --rmi all --volumes", check=False)
    
    print("✅ Cleanup completed")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Docker management for Flask Server")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build command
    build_parser = subparsers.add_parser('build', help='Build Docker image')
    build_parser.add_argument('--tag', default='user-management-server', help='Image tag')
    build_parser.add_argument('--dockerfile', default='docker/Dockerfile', help='Dockerfile path')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run Docker container')
    run_parser.add_argument('--tag', default='user-management-server', help='Image tag')
    run_parser.add_argument('--port', type=int, default=5000, help='Port to expose')
    run_parser.add_argument('--name', default='flask-server', help='Container name')
    run_parser.add_argument('-d', '--detached', action='store_true', help='Run in background')
    
    # Compose commands
    compose_up_parser = subparsers.add_parser('up', help='Run docker-compose up')
    compose_up_parser.add_argument('-d', '--detached', action='store_true', help='Run in background')
    compose_up_parser.add_argument('--build', action='store_true', help='Build images before starting')
    compose_up_parser.add_argument('--env', choices=['dev', 'prod'], default='prod', help='Environment (dev/prod)')
    
    compose_down_parser = subparsers.add_parser('down', help='Run docker-compose down')
    compose_down_parser.add_argument('--env', choices=['dev', 'prod'], default='prod', help='Environment (dev/prod)')
    subparsers.add_parser('status', help='Show container status')
    subparsers.add_parser('cleanup', help='Clean up Docker resources')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'build':
            build_image(args.tag, args.dockerfile)
        elif args.command == 'run':
            run_container(args.tag, args.port, args.name, args.detached)
        elif args.command == 'up':
            compose_up(args.detached, args.build, args.env)
        elif args.command == 'down':
            compose_down(args.env)
        elif args.command == 'status':
            show_status()
        elif args.command == 'cleanup':
            cleanup()
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)

if __name__ == '__main__':
    main()