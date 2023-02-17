' Set the target directory to traverse
strTargetDir = "C:\Example\Directory"

' Create the CSV file to output to
Set objCSVFile = CreateObject("Scripting.FileSystemObject").OpenTextFile("output.csv", 2, True)
objCSVFile.WriteLine("Directory 1,Directory 2,File Name,Full Path,File Size (bytes),MIME Content Type")

' Call the recursive function to traverse the directory
TraverseDirectory strTargetDir, objCSVFile

' Close the CSV file
objCSVFile.Close

' Recursive function to traverse the directory and output file information
Sub TraverseDirectory(strDirPath, objCSVFile)
    ' Get a reference to the current directory object
    Set objDir = CreateObject("Scripting.FileSystemObject").GetFolder(strDirPath)
    
    ' Loop through all the files in the current directory
    For Each objFile In objDir.Files
        ' Separate the directory name into two fields based on the pattern
        arrDir = Split(objDir.Name, "(")
        strDir1 = arrDir(0)
        strDir2 = Replace(arrDir(1), ")", "")
        
        ' Get the file size in bytes
        lngFileSize = objFile.Size
        
        ' Get the MIME content type of the file
        strContentType = GetContentType(objFile.Path)
        
        ' Output the file information to the CSV file
        objCSVFile.WriteLine(strDir1 & "," & strDir2 & "," & objFile.Name & "," & objFile.Path & "," & lngFileSize & "," & strContentType)
    Next
    
    ' Recursively call this function on all the subdirectories of the current directory
    For Each objSubDir In objDir.SubFolders
        TraverseDirectory objSubDir.Path, objCSVFile
    Next
End Sub

' Function to get the MIME content type of a file
Function GetContentType(strFilePath)
    ' Create a new ADODB.Stream object
    Set objStream = CreateObject("ADODB.Stream")
    
    ' Set the type of the stream to binary
    objStream.Type = 1
    
    ' Open the file and load its contents into the stream object
    objStream.Open
    objStream.LoadFromFile strFilePath
    
    ' Get the MIME content type of the file from the stream object
    strContentType = objStream.TypeInfo
    
    ' Clean up and return the content type
    objStream.Close
    Set objStream = Nothing
    GetContentType = strContentType
End Function
