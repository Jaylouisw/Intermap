"""
Command-line interface for manual traceroute operations
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.traceroute.tracer import trace_to_target, trace_subnet, Traceroute
from src.graph.gexf_generator import NetworkGraph, GEXFGenerator, create_gexf_from_traceroutes
from src.utils import is_public_ip


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def traceroute_command(args):
    """Handle traceroute command."""
    logger = logging.getLogger(__name__)
    
    target = args.target
    
    # Security check
    if not is_public_ip(target):
        logger.error(f"Target {target} is not a public IP address!")
        logger.error("Intermap only traces public IPs to protect privacy.")
        return 1
    
    logger.info(f"Tracing route to {target}...")
    
    result = trace_to_target(target, filter_private=True)
    
    if result['hop_count'] == 0:
        logger.warning("No hops found (or all hops were private)")
        return 1
    
    # Display results
    print(f"\nTraceroute to {result['target']}")
    print(f"Found {result['hop_count']} public hops:\n")
    
    for hop in result['hops']:
        hop_num = hop['hop']
        ip = hop['ip']
        hostname = hop.get('hostname') or ip
        rtt = hop.get('rtt', 0)
        print(f"  {hop_num:2d}. {ip:15s} ({hostname}) - {rtt:.2f}ms")
    
    # Save to GEXF if requested
    if args.output:
        logger.info(f"Saving to GEXF: {args.output}")
        create_gexf_from_traceroutes([result], args.output)
        print(f"\nSaved to {args.output}")
    
    return 0


def subnet_command(args):
    """Handle subnet traceroute command."""
    logger = logging.getLogger(__name__)
    
    subnet = args.subnet
    
    logger.info(f"Tracing subnet: {subnet}")
    logger.warning("This may take a while depending on subnet size...")
    
    results = trace_subnet(subnet, max_targets=args.max_targets)
    
    if not results:
        logger.error("No successful traces in subnet")
        return 1
    
    print(f"\nCompleted {len(results)} successful traces")
    
    # Save to GEXF if requested
    if args.output:
        logger.info(f"Saving aggregated graph to: {args.output}")
        create_gexf_from_traceroutes(results, args.output)
        print(f"Saved to {args.output}")
    else:
        # Display summary
        total_hops = sum(r['hop_count'] for r in results)
        print(f"Total hops discovered: {total_hops}")
        print("\nUse --output <file.gexf> to save the graph")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Intermap - Manual Traceroute Tool',
        epilog='PRIVACY: Only public IPs are traced. Private IPs are filtered.'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Traceroute command
    trace_parser = subparsers.add_parser(
        'trace',
        help='Trace route to a specific IP address'
    )
    trace_parser.add_argument(
        'target',
        help='Target IP address (must be public)'
    )
    trace_parser.add_argument(
        '--output', '-o',
        help='Save results to GEXF file'
    )
    
    # Subnet command
    subnet_parser = subparsers.add_parser(
        'subnet',
        help='Trace all IPs in a subnet (public IPs only)'
    )
    subnet_parser.add_argument(
        'subnet',
        help='Subnet in CIDR notation (e.g., 8.8.8.0/28)'
    )
    subnet_parser.add_argument(
        '--max-targets',
        type=int,
        default=50,
        help='Maximum number of IPs to trace (default: 50)'
    )
    subnet_parser.add_argument(
        '--output', '-o',
        help='Save aggregated graph to GEXF file'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handler
    if args.command == 'trace':
        return traceroute_command(args)
    elif args.command == 'subnet':
        return subnet_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
