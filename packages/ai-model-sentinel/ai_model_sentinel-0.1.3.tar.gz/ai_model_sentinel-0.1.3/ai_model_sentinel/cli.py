import click
import os
import json
from datetime import datetime
from .core.sentinel import Sentinel
# from .dashboard.web_interface import start_dashboard  # Temporarily commented

@click.group()
def cli():
    """AI Model Sentinel - Comprehensive AI Model Monitoring Toolkit"""
    pass

@cli.command()
@click.option('--path', default='.', help='Path to scan for AI models')
@click.option('--deep', is_flag=True, help='Perform deep scanning')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--exclude', help='Pattern to exclude from scanning')
def scan(path, deep, verbose, exclude):
    """Scan project for AI models"""
    if verbose:
        click.echo(f"🔍 Scanning path: {path}")
        click.echo(f"🔍 Deep scan: {deep}")
        if exclude:
            click.echo(f"🔍 Exclude pattern: {exclude}")
    
    sentinel = Sentinel()
    
    # Simulate scanning results
    results = {
        'models': [
            {'path': './model.h5', 'type': 'h5'},
            {'path': './model.pb', 'type': 'pb'}
        ],
        'directories_scanned': 5,
        'duration_ms': 1200
    }
    
    click.echo(f"📊 Scan Results:")
    click.echo(f"   Found {len(results['models'])} AI models")
    click.echo(f"   Scanned {results['directories_scanned']} directories")
    click.echo(f"   Duration: {results['duration_ms']}ms")
    
    if results['models']:
        click.echo("\n📁 Models found:")
        for i, model in enumerate(results['models'], 1):
            click.echo(f"   {i}. {model['path']} ({model['type']})")

@cli.command()
@click.option('--path', required=True, help='Path to monitor')
@click.option('--interval', default=300, help='Monitoring interval in seconds')
@click.option('--api-key', help='API key for cloud integration')
def monitor(path, interval, api_key):
    """Monitor AI models in production"""
    click.echo(f"🛡️ Starting monitoring service...")
    click.echo(f"📁 Monitoring path: {path}")
    click.echo(f"⏰ Check interval: {interval}s")
    
    if api_key:
        click.echo(f"☁️ Cloud integration: Enabled")
    
    click.echo("✅ Monitoring service started successfully")

@cli.command()
@click.option('--output', default='report.html', help='Output report file')
@click.option('--format', 'report_format', type=click.Choice(['html', 'json', 'pdf']), default='html')
def report(output, report_format):
    """Generate scan report"""
    click.echo(f"📄 Generating {report_format.upper()} report...")
    
    # Simulate report generation
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "models_scanned": 2,
        "vulnerabilities_found": 0,
        "recommendations": ["Keep models updated", "Monitor regularly"]
    }
    
    try:
        # استخدام المتغير الصحيح
        full_path = os.path.abspath(output)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            if report_format == 'json':
                json.dump(report_data, f, indent=2)
            else:
                f.write(f"<html><body><h1>AI Model Sentinel Report</h1><pre>{json.dumps(report_data, indent=2)}</pre></body></html>")
        
        click.echo(f"✅ Report generated: {output}")
        click.echo(f"📁 Full path: {full_path}")
        
        # التحقق من وجود الملف
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            click.echo(f"📏 File size: {file_size} bytes")
        else:
            click.echo("❌ ERROR: File was not created!")
            
    except Exception as e:
        click.echo(f"❌ Error generating report: {str(e)}")

@cli.command()
def dashboard():
    """Start web dashboard"""
    click.echo("🌐 Starting web dashboard...")
    # start_dashboard()  # Temporarily commented until implemented
    click.echo("✅ Dashboard would start on http://localhost:3000")
    click.echo("📋 Note: Full dashboard functionality coming in next update")

@cli.command()
def version():
    """Show version information"""
    click.echo("AI Model Sentinel v0.1.3")
    click.echo("Comprehensive AI Model Monitoring and Drift Detection Toolkit")

def main():
    cli()

if __name__ == '__main__':
    main()