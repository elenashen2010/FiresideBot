IF EXIST %SYSTEMROOT%\py.exe (
    CMD /k py.exe red.py
    EXIT
)

CMD /k python red.py
pause