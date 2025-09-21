#!/usr/bin/env python3
"""
Fukui_Net CLI Module

Command-line interface for predicting Fukui indices using the trained Fukui_Net model.
"""

import os

import torch
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from fukui_net.predictor import FukuiNetPredictor

app = typer.Typer(help="Predict Fukui indices using Fukui_Net")
console = Console()


@app.command()
def predict(
    smiles: str | None = typer.Argument(None, help="SMILES string to predict"),
    csv_file: str | None = typer.Option(None, "--csv", "-c", help="CSV file with SMILES column"),
    output_file: str | None = typer.Option(None, "--output", "-o", help="Output CSV file (required with --csv)"),
    smiles_column: str = typer.Option("smiles", "--column", help="Name of SMILES column in CSV"),
    checkpoint: str = typer.Option("models/final_model.ckpt", "--checkpoint", help="Path to model checkpoint"),
    device: str = typer.Option("auto", "--device", "-d", help="Device to use (cpu, cuda, cuda:1, etc.)")
):
    """Predict Fukui indices for molecules."""

    # Check if checkpoint exists
    if not os.path.exists(checkpoint):
        console.print(f"[red]Error: Checkpoint file not found: {checkpoint}[/red]")
        raise typer.Exit(1)

    # Initialize predictor
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Loading model..."),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Loading model", total=None)
            predictor = FukuiNetPredictor(checkpoint, device)
            progress.update(task, completed=True)

        console.print(f"[green]✓ Model loaded successfully on {predictor.device}[/green]")
    except Exception as e:
        console.print(f"[red]Error loading model: {e}[/red]")
        raise typer.Exit(1) from e

    # Perform prediction
    if smiles:
        # Single molecule prediction
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold blue]Predicting Fukui indices for: {smiles}..."),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Predicting", total=None)
                predictions = predictor.predict_smiles(smiles)
                progress.update(task, completed=True)

            console.print(f"[bold blue]Fukui indices:[/bold blue] {predictions}")

        except Exception as e:
            console.print(f"[red]Error predicting molecule: {e}[/red]")
            raise typer.Exit(1) from e

    elif csv_file:
        # Batch prediction from CSV
        if not output_file:
            console.print("[red]Error: --output is required when using --csv[/red]")
            raise typer.Exit(1)

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold blue]Processing batch from {csv_file}..."),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Processing batch", total=None)
                predictor.predict_from_csv(csv_file, output_file, smiles_column)
                progress.update(task, completed=True)

            console.print(f"[green]✓ Predictions saved to {output_file}[/green]")
        except Exception as e:
            console.print(f"[red]Error processing batch: {e}[/red]")
            raise typer.Exit(1) from e

    else:
        console.print("[red]Please provide either SMILES string or --csv file[/red]")
        console.print("\n[yellow]Examples:[/yellow]")
        console.print("  uv run fukui_net predict \"CCO\"")
        console.print("  uv run fukui_net predict --csv molecules.csv --output predictions.csv")
        console.print("  uv run fukui_net predict \"CCO\" --device cuda:1")
        raise typer.Exit(1)


@app.command()
def info():
    """Show information about available devices and model."""
    console.print("[bold blue]Fukui_Net Model Information[/bold blue]")

    # Device information
    table = Table(title="Available Devices")
    table.add_column("Device", style="cyan")
    table.add_column("Available", style="green")
    table.add_column("Name", style="yellow")
    table.add_column("Memory (GB)", style="magenta")

    table.add_row("CPU", "✓", "CPU", "-")

    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            device_name = torch.cuda.get_device_name(i)
            memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            table.add_row(f"cuda:{i}", "✓", device_name, f"{memory:.1f}")
    else:
        table.add_row("CUDA", "✗", "Not available", "-")

    console.print(table)

    # Model information
    checkpoint_path = "models/final_model.ckpt"
    if os.path.exists(checkpoint_path):
        console.print(f"\n[green]✓ Model checkpoint found: {checkpoint_path}[/green]")
        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
        console.print(f"  Epochs trained: {checkpoint.get('epoch', 'Unknown')}")
        console.print(f"  Global steps: {checkpoint.get('global_step', 'Unknown')}")
        console.print(f"  PyTorch Lightning version: {checkpoint.get('pytorch-lightning_version', 'Unknown')}")
    else:
        console.print(f"\n[red]✗ Model checkpoint not found: {checkpoint_path}[/red]")


if __name__ == "__main__":
    app()
