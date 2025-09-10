$FACTORY = "C:\Users\Sergey\Documents\TSA-Ingenic\MK3\factory\15.04.25\firmware_tsa9.tar"

$hello = "echo ""HELLO FROM THE DEVICE!"""


# Function to execute an ADB shell command and handle its output
function ExecuteCommand {
    param (
        [Parameter(Mandatory=$true)] # Make the command parameter mandatory
        [string]$Command             # The command string to execute on the device
    )

    Write-Host "Executing command: adb shell '$Command'"
    $result = adb shell "$Command"

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

function HelloFromDevice {
    # Check if a response was received. If not, write an error and exit.
    $resp = ExecuteCommand "echo ""HELLO FROM THE DEVICE!"""
    if (-not ($resp)) {
        Write-Error "Error: No response received from the device after initial HELLO command."
        exit 1 # Exit with a non-zero code to indicate an error
    } else {
        Write-Host "Initial device response: $($resp)"
    }
}


# Function to save UUID and current time to files on the device
function SaveUuidAndTime {
    $uuid = (New-Guid).ToString()
    $currentTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")

    # Construct the commands to echo the UUID and time into files on the device
    # Note: PowerShell will expand $uuid and $currentTime before sending the string to adb shell
    # The inner quotes are escaped (`") to ensure they are passed to the remote shell.
    $uuidCommand = "echo `"$uuid`" > /usr/mmcdata/mmcblk0p8/uuid.txt"
    $timeCommand = "echo `"$currentTime`" > /usr/mmcdata/mmcblk0p8/time.txt"

    # Execute the commands using the ExecuteCommand function
    # if (-not (ExecuteCommand $uuidCommand)) { return $false }
    # if (-not (ExecuteCommand $timeCommand)) { return $false }
    ExecuteCommand $uuidCommand
    ExecuteCommand $timeCommand

    ExecuteCommand "cat /usr/mmcdata/mmcblk0p8/uuid.txt"
    ExecuteCommand "cat /usr/mmcdata/mmcblk0p8/time.txt"

    Write-Host "UUID and Time saved successfully to device."
    return $true
}

# Function to prepare the device's storage for upload
function PrepareDeviceForUpload {
    # Execute a series of commands to unmount, format, and remount the partition
    # Each command's success is checked by the ExecuteCommand function

    # if (-not (ExecuteCommand "umount /usr/mmcdata/mmcblk0p8")) { return $false }
    # if (-not (ExecuteCommand "mkfs.vfat /dev/mmcblk0p8")) { return $false }
    # if (-not (ExecuteCommand "mount /dev/mmcdata/mmcblk0p8 /usr/mmcdata/mmcblk0p8")) { return $false }
    ExecuteCommand "umount /usr/mmcdata/mmcblk0p8"
    ExecuteCommand "mkfs.vfat /dev/mmcblk0p8"
    ExecuteCommand "mount /dev/mmcdata/mmcblk0p8 /usr/mmcdata/mmcblk0p8"

    # If all previous commands succeed, then save UUID and time
    SaveUuidAndTime # This function will need its parameters passed when called from here
    return $true # Indicate overall success of preparation
}


function PushFileToDevice {
    PrepareDeviceForUpload

    $remoteFilename = "/usr/mmcdata/mmcblk0p8/firmware.tar"
    $result = adb push $FACTORY $remoteFilename
    if (-not ($result)) { 
        Write-Error "Error: No response received from the device after push command."
        exit 1 # Exit with a non-zero code to indicate an error
    } else {
        Write-Host $result
    }
}


function RunFirmwareUpdateCommand {
    ExecuteCommand "tar -xvf /usr/mmcdata/mmcblk0p8/firmware.tar -C /"
    ExecuteCommand "sync"
    ExecuteCommand "ls -l /"
    ExecuteCommand "chmod +x /firmware.sh"
    ExecuteCommand "/firmware.sh"
}


HelloFromDevice
PushFileToDevice
RunFirmwareUpdateCommand