import React from 'react';

interface MarkdownTextProps {
  text: string;
  className?: string;
}

export function MarkdownText({ text, className = '' }: MarkdownTextProps) {
  // Parse simple markdown patterns
  const parseMarkdown = (text: string) => {
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    let key = 0;

    // Pattern for **bold**
    const boldRegex = /\*\*(.+?)\*\*/g;
    let match;

    while ((match = boldRegex.exec(text)) !== null) {
      // Add text before the match
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }
      
      // Add bold text
      parts.push(
        <strong key={`bold-${key++}`} className="font-semibold text-primary">
          {match[1]}
        </strong>
      );
      
      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  // Split by newlines to handle paragraphs and lists
  const lines = text.split('\n');
  
  return (
    <div className={className}>
      {lines.map((line, index) => {
        const trimmedLine = line.trim();
        
        // Handle bullet points
        if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-')) {
          const content = trimmedLine.substring(1).trim();
          return (
            <div key={index} className="flex items-start gap-2 my-1">
              <span className="text-sage mt-0.5">•</span>
              <span className="flex-1">{parseMarkdown(content)}</span>
            </div>
          );
        }
        
        // Handle numbered lists
        if (/^\d+\./.test(trimmedLine)) {
          const content = trimmedLine.replace(/^\d+\./, '').trim();
          return (
            <div key={index} className="flex items-start gap-2 my-1">
              <span className="text-sage mt-0.5">{trimmedLine.match(/^\d+/)?.[0]}.</span>
              <span className="flex-1">{parseMarkdown(content)}</span>
            </div>
          );
        }
        
        // Empty line
        if (trimmedLine === '') {
          return <div key={index} className="h-2" />;
        }
        
        // Regular paragraph
        return (
          <p key={index} className="my-1">
            {parseMarkdown(line)}
          </p>
        );
      })}
    </div>
  );
}
