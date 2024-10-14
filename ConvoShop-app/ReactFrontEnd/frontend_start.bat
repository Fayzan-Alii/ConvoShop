@echo off

SET NODE_OPTIONS=--openssl-legacy-provider
call npm install
call npm start

pause
