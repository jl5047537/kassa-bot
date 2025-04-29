[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PGCLIENTENCODING='UTF8'
psql "postgresql://postgres:postgres123@localhost:5432/kassa_bot" -c "SELECT 1;" 