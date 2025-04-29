# Установка кодировки UTF-8 в реестре
$registryPath = "HKCU:\Console"
$name = "CodePage"
$value = 65001  # UTF-8

# Создаем или обновляем значение в реестре
if (!(Test-Path $registryPath)) {
    New-Item -Path $registryPath -Force | Out-Null
}
Set-ItemProperty -Path $registryPath -Name $name -Value $value -Type DWord

# Применяем настройки к текущей сессии
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Настройки кодировки применены. Пожалуйста, перезапустите PowerShell для применения изменений." 