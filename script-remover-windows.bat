@echo off
setlocal enabledelayedexpansion

rem Defina as imagens desejadas
set "IMAGES=container-vog-fornecedor container-vog-almoxarifado container-vog-fabrica container-vog-linha container-vog-ordem"

for %%i in (%IMAGES%) do (
    for /f "tokens=*" %%j in ('docker ps -a --format "{{.ID}} {{.Image}}"') do (
        for /f "tokens=1,2" %%a in ("%%j") do (
            set "CONTAINER_ID=%%a"
            set "CONTAINER_IMAGE=%%b"

            if "!CONTAINER_IMAGE!"=="%%i" (
                echo Removendo container !CONTAINER_ID! relacionado a %%i
                docker stop !CONTAINER_ID! && docker rm !CONTAINER_ID!
            )
        )
    )
)

endlocal