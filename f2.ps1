# Function to execute an ADB shell command and handle its output
function ExecuteCommand {
    param (
        [Parameter(Mandatory=$true)] # Make the command parameter mandatory
        [string]$Command             # The command string to execute on the device
    )

    Write-Host "Executing command: adb shell '$Command'"
    # $result = adb shell "$Command"

    $result = adb shell "$Command"

    # $getLastExitCodeCommand = "echo \$?"
    # $code = adb shell "$getLastExitCodeCommand"
    # $code = $code.Trim()
    # Write-Host "Output: $($code)"
    # if ($code -eq "0") {
    #     Write-Host "Remote command '$Command' succeeded (exit code 0)."
    # } else {
    #     Write-Host "Remote command '$Command' failed with exit code: $code"
    # }

    # Check if the command returned any output (indicating potential success or specific output)
    if (-not $result) {
        Write-Warning "Command 'adb shell $Command' returned no output."
        # Depending on the command, no output might be expected, or it might be an error.
        # You might want to add more specific error checking here if adb shell returns error codes.
        return $false # Indicate failure
    } else {
        Write-Host "Command output: $($result)"
        return $result # Indicate success
    }
}


ExecuteCommand "ls /"