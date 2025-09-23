# pyass🍑/tests/test_cli.py

import subprocess

def test_cli_help():
    """Test CLI help command"""
    cli_path = "/home/wraithsphinx/Applications/pyass/pyass/bin/pyass"
    result = subprocess.run([cli_path, "--help"], capture_output=True, text=True)
    assert result.returncode == 0, "CLI should exit with 0"
    assert "pyass🍑" in result.stdout, "Help should mention pyass🍑"

def test_cli_define():
    """Test define command"""
    cli_path = "/home/wraithsphinx/Applications/pyass/pyass/bin/pyass"
    result = subprocess.run([cli_path, "define", "rizz"], capture_output=True, text=True)
    assert result.returncode == 0, "Define should succeed"
    assert "charisma" in result.stdout.lower(), "Should show rizz definition"

def test_cli_translate():
    """Test translate command"""
    cli_path = "/home/wraithsphinx/Applications/pyass/pyass/bin/pyass"
    result = subprocess.run([
        cli_path, "translate",
        "This is good", "--intensity", "1.0"
    ], capture_output=True, text=True)
    assert result.returncode == 0, "Translate should succeed"
    # Find the translated line
    translated_line = None
    for line in result.stdout.splitlines():
        if "translated:" in line.lower():
            translated_line = line.lower()
            break
    assert translated_line is not None, "No translated line found in output"
    assert "good" not in translated_line, "Should translate 'good'"
