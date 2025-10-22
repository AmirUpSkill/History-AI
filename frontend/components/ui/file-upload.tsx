
"use client"

import React, { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, X, FileText } from "lucide-react"
import { cn } from "@/lib/utils"

interface FileUploadProps {
  value?: File | null
  onChange: (file?: File | null) => void
  className?: string
}

export function FileUpload({ value, onChange, className }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onChange(acceptedFiles[0])
    }
    setDragActive(false)
  }, [onChange])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"]
    },
    maxFiles: 1,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
  })

  const handleRemoveFile = (e: React.MouseEvent) => {
    e.stopPropagation()
    onChange(undefined)
  }

  return (
    <div
      {...getRootProps()}
      className={cn(
        "relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
        dragActive || isDragActive
          ? "border-primary bg-primary/5"
          : "border-border hover:border-primary/50",
        className
      )}
    >
      <input {...getInputProps()} />
      
      {value ? (
        <div className="flex items-center justify-between p-2 bg-secondary/30 rounded">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium truncate max-w-[200px]">
              {value.name}
            </span>
            <span className="text-xs text-muted-foreground">
              ({(value.size / 1024 / 1024).toFixed(2)} MB)
            </span>
          </div>
          <button
            type="button"
            onClick={handleRemoveFile}
            className="p-1 rounded-full hover:bg-destructive/10 text-destructive"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-2 text-muted-foreground">
          <Upload className="h-10 w-10" />
          <div className="text-sm">
            <span className="font-semibold">Click to upload</span> or drag and drop
          </div>
          <p className="text-xs">PDF (MAX. 5MB)</p>
        </div>
      )}
    </div>
  )
}