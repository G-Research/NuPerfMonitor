#########################################################
$dotnet_base_url = "https://download.visualstudio.microsoft.com/download/pr/2b2d6133-c4f9-46dd-9ab6-86443a7f5783/340054e2ac7de2bff9eea73ec9d4995a/dotnet-sdk-8.0.100-win-x64.zip"
$dotnet_url = Get-Content -Path $PSScriptRoot\daily-windows.txt
$repoUrl = "https://github.com/NuGet/NuGet.Client.git"
$commitHash = "2a15947b853fcaa7804743f9e171d7824cf2f775"
$solutionFilePath = "NuGet.sln"
$globalJsonPath = "global.json"

#########################################################
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\..\PerformanceTestUtilities.ps1"

$repoName = GenerateNameFromGitUrl $repoUrl
$resultsFilePath = "results.csv"
$sourcePath = $([System.IO.Path]::GetFullPath($repoName))
SetupGitRepository $repoUrl $commitHash $sourcePath
$solutionFilePath = "$sourcePath\$solutionFilePath"
$ProgressPreference = 'SilentlyContinue' #https://github.com/PowerShell/PowerShell/issues/2138 
if ($globalJsonPath) {Remove-Item "$sourcePath\$globalJsonPath"}

#########################################################
# Workaround for:
# - https://learn.microsoft.com/en-us/nuget/reference/errors-and-warnings/nu1510
Add-Content -Path "$sourcePath\Directory.Build.rsp" -Value "/p:NoWarn=NU1510`r`n"
Add-Content -Path "$sourcePath\Directory.Build.rsp" -Value "/p:CheckEolTargetFramework=false`r`n"

$versions = @("dotnet_base", "dotnet")
ForEach ($version In $versions) {
	. "$version\dotnet.exe" --info
	$url = (Get-Variable ("$version" + "_url")).Value
	Invoke-WebRequest -Uri "$url" -OutFile ("$version" + ".zip")
    Expand-Archive ("$version" + ".zip") -DestinationPath "$version"
	. "$PSScriptRoot\..\RunPerformanceTests.ps1" -nugetClientFilePath "$version\dotnet.exe" -solutionFilePath $solutionFilePath -resultsFilePath $resultsFilePath -iterationCount 1
}