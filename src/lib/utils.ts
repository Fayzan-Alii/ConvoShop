import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import React from 'react';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Function to wrap each character in a span for letter-by-letter animations
export function wrapTextInSpans(text: string): React.ReactNode[] {
  return text.split('').map((char, index) => (
    React.createElement('span', { key: index, className: "inline-block" }, 
      char === ' ' ? '\u00A0' : char
    )
  ));
}