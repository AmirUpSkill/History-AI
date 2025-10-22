"use client"

import React, { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { toast } from "sonner"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { FileUpload } from "@/components/ui/file-upload"
import { useAppStore } from "@/store/app-store"
import { createCardSchema, type CreateCardFormData } from "@/lib/validators"

export function AddCardDialog() {
  const {
    isAddCardDialogOpen,
    isCreatingCard,
    createCardError,
    closeAddCardDialog,
    createNewCard,
    resetCreateCardState,
  } = useAppStore()

  const form = useForm<CreateCardFormData>({
    resolver: zodResolver(createCardSchema),
    defaultValues: {
      title: "",
      system_prompt: "",
      topics_to_cover: "",
      context_file: undefined,
    },
  })

  useEffect(() => {
    if (isAddCardDialogOpen) {
      form.reset()
      resetCreateCardState()
    }
  }, [isAddCardDialogOpen, form, resetCreateCardState])

  const onSubmit = async (data: CreateCardFormData) => {
    const success = await createNewCard(data)
    if (success) {
      toast.success("Card created successfully!")
      form.reset()
    } else {
      toast.error("Failed to create card. Please try again.")
    }
  }

  return (
    <Dialog open={isAddCardDialogOpen} onOpenChange={closeAddCardDialog}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Card</DialogTitle>
          <DialogDescription>
            Add a new historical event card. AI will generate the content based on your input.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="title" className="text-sm font-medium">
              Title
            </label>
            <Input
              id="title"
              placeholder="Enter the title of the event"
              {...form.register("title")}
              disabled={isCreatingCard}
            />
            {form.formState.errors.title && (
              <p className="text-sm text-destructive">
                {form.formState.errors.title.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="system_prompt" className="text-sm font-medium">
              System Prompt
            </label>
            <Textarea
              id="system_prompt"
              placeholder="Provide instructions for AI to generate content"
              rows={3}
              {...form.register("system_prompt")}
              disabled={isCreatingCard}
            />
            {form.formState.errors.system_prompt && (
              <p className="text-sm text-destructive">
                {form.formState.errors.system_prompt.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="topics_to_cover" className="text-sm font-medium">
              Topics to Cover
            </label>
            <Textarea
              id="topics_to_cover"
              placeholder="List the topics that should be covered in this card"
              rows={2}
              {...form.register("topics_to_cover")}
              disabled={isCreatingCard}
            />
            {form.formState.errors.topics_to_cover && (
              <p className="text-sm text-destructive">
                {form.formState.errors.topics_to_cover.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">
              Context File (Optional)
            </label>
            <FileUpload
              value={form.watch("context_file")}
              onChange={(file) => form.setValue("context_file", file)}
            />
            {form.formState.errors.context_file && (
              <p className="text-sm text-destructive">
                {form.formState.errors.context_file.message}
              </p>
            )}
          </div>

          {createCardError && (
            <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
              {createCardError}
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={closeAddCardDialog}
              disabled={isCreatingCard}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isCreatingCard}>
              {isCreatingCard ? "Creating..." : "Create Card"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}