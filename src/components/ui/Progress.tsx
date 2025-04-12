import * as React from "react";
import { useTheme } from '@/lib/ThemeContext';

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number | null | undefined;
  max?: number;
  className?: string;
}

export const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ value, max = 100, className = "", ...props }, ref) => {
    const { theme } = useTheme();
    
    const isIndeterminate = value === undefined || value === null;
    
    return (
      <div
        ref={ref}
        className={`h-2 w-full overflow-hidden rounded-full ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-200'} ${className}`}
        {...props}
      >
        {isIndeterminate ? (
          <div className="h-full w-full origin-left-right animate-indeterminate-progress bg-gradient-to-r from-indigo-500 to-purple-500" />
        ) : (
          <div
            className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500 ease-in-out"
            style={{ width: `${Math.min(Math.max(0, value), max) / max * 100}%` }}
          />
        )}
      </div>
    );
  }
);

Progress.displayName = "Progress";