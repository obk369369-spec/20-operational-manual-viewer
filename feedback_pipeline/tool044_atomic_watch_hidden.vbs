Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
shell.Run Chr(34) & folder & "\tool044_atomic_watch_start.cmd" & Chr(34), 0, False
