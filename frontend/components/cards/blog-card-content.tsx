"use client"

import * as React from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeRaw from "rehype-raw"
import rehypeSanitize from "rehype-sanitize"

const getText = (children: React.ReactNode): string =>
  React.Children.toArray(children)
    .map((child: any) =>
      typeof child === "string" ? child : typeof child?.props?.children === "string" ? child.props.children : child?.props?.children ? getText(child.props.children) : ""
    )
    .join("")

const slugify = (children: React.ReactNode) =>
  getText(children).toLowerCase().trim().replace(/[^a-z0-9\s-]/g, "").replace(/\s+/g, "-").replace(/-+/g, "-")

export function BlogCardContent({ content }: { content: string }) {
  if (!content?.trim()) return <p className="text-foreground/70">Content is not available for this card yet.</p>
  
  const processedContent = content.replace(/\\n/g, '\n')

  const H = (Tag: React.ElementType, cls: string) => ({ children, ...props }: any) => {
    const id = slugify(children)
    return (
      <Tag id={id} className={`${cls} scroll-mt-24`} {...props}>
        {children}
      </Tag>
    )
  }

  return (
    <article className="markdown-content max-w-none prose-lg">
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]} 
        rehypePlugins={[rehypeRaw, rehypeSanitize]}
        components={{
        h1: H("h1", "text-4xl font-extrabold text-primary mb-6 mt-10 first:mt-0 tracking-tight"),
        h2: H("h2", "text-3xl font-bold text-primary mb-5 mt-10 tracking-tight"),
        h3: H("h3", "text-2xl font-semibold text-primary mb-4 mt-8"),
        h4: H("h4", "text-xl font-semibold text-primary mb-3 mt-6"),
        h5: H("h5", "text-lg font-semibold text-primary mb-3 mt-5"),
        h6: H("h6", "text-base font-semibold text-primary mb-2 mt-4"),
        p: ({ ...props }) => <p className="text-foreground/85 leading-[1.8] mb-6 text-[1.0625rem]" {...props} />,
        ul: ({ ...props }) => <ul className="list-disc pl-8 space-y-2.5 mb-6 text-foreground/85 marker:text-primary/60" {...props} />,
        ol: ({ ...props }) => <ol className="list-decimal pl-8 space-y-2.5 mb-6 text-foreground/85 marker:text-primary/60 marker:font-semibold" {...props} />,
        li: ({ checked, children, ...props }: any) => (
          <li className="leading-[1.8] pl-2" {...props}>
            {typeof checked === "boolean" && <input type="checkbox" className="mr-2 align-middle accent-accent" checked={checked} readOnly />}
            {children}
          </li>
        ),
        table: ({ ...props }) => <div className="overflow-x-auto my-6 rounded-lg border border-border/50"><table className="w-full text-sm" {...props} /></div>,
        thead: ({ ...props }) => <thead className="bg-secondary/40" {...props} />,
        tr: ({ ...props }) => <tr className="border-b border-border/30" {...props} />,
        th: ({ ...props }) => <th className="px-4 py-3 text-left font-semibold text-primary border-b-2 border-border" {...props} />,
        td: ({ ...props }) => <td className="px-4 py-3 align-top text-foreground/80" {...props} />,
        img: ({ ...props }) => <img className="rounded-lg my-6 max-w-full h-auto shadow-md" loading="lazy" alt={props.alt || ""} {...props} />,
        blockquote: ({ ...props }) => <blockquote className="border-l-4 border-accent pl-5 pr-4 py-3 my-6 italic text-foreground/75 bg-secondary/10 rounded-r-lg" {...props} />,
        code: ({ inline, className, children, ...props }: any) => inline ? 
          <code className="bg-secondary/40 text-primary px-1.5 py-0.5 rounded text-[0.9em] font-mono border border-border/30" {...props}>{children}</code> :
          <pre className="bg-secondary/20 text-foreground p-4 rounded-lg overflow-x-auto text-sm font-mono my-6 border border-border/30"><code className={className} {...props}>{children}</code></pre>,
        a: ({ ...props }) => <a className="text-accent hover:text-accent/80 underline underline-offset-2 transition-colors font-medium" target="_blank" rel="noopener noreferrer" {...props} />,
        hr: ({ ...props }) => <hr className="my-8 border-t-2 border-border/50" {...props} />,
        strong: ({ ...props }) => <strong className="font-bold text-primary/95" {...props} />,
        em: ({ ...props }) => <em className="italic text-foreground/90" {...props} />,
        del: ({ ...props }) => <del className="line-through text-foreground/60" {...props} />,
      }}>
        {processedContent}
      </ReactMarkdown>
    </article>
  )
}
