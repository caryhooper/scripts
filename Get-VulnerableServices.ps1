#Function to enumerate services and check for vulnerabilities
#Cary Hooper
#02-01-2018

#Check to see if we can modify service path
function Check-ServicePathPermission($service){ #input a service object
    $servicepath = $service.pathname
    $newservicepath = $servicepath + " #"
    #Try changing the service path
    try {$test = $service  | Invoke-WmiMethod -Name Change -ArgumentList @($null,$null,$null,$null,$null,$newservicepath)}
    catch {}
    #Put back to normal
    try {$test2 = $service  | Invoke-WmiMethod -Name Change -ArgumentList @($null,$null,$null,$null,$null,$servicepath)}
    catch {}
    if ($test.ReturnValue -eq 0){
        Write-Host "        VULNERABLE: Current user can change the " $service.Name " service path."
    }
}

#Check to see if we can modify the binary
function Check-BinaryPermission($service){ #input a service object
    $filepath = $service.pathname.Split(" ")[0]
    $error.clear()
    #Try to open/close the binary
    try{
        "" | Out-File $filepath -Append
    }
    catch {}
    #If we can, then current user has permissions.
    if (!$error){
        Write-Host "        VULNERABLE: The file called by " $service.Name "may be modified by current user. Path - " $filepath
    }
}
function Get-VulnerableServices{
    Write-Host "Checking to see if any services are exploitable..."
    $allservices = Get-WmiObject win32_service
    $allservices | %{
        #Write-Host "Checking " $_.Name 
        Check-BinaryPermission($_)
        Check-ServicePathPermission($_)
    }
    Write-Host "Script has completed."
}

Get-VulnerableServices
