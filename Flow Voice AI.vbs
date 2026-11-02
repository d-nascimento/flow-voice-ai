Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
strPython = strScriptDir & "\.venv\Scripts\python.exe"

' Executa sem abrir qualquer janela preta de terminal (0 = oculto)
WshShell.CurrentDirectory = strScriptDir
WshShell.Run """" & strPython & """ -m src.app", 0, False
