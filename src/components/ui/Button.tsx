import { ButtonHTMLAttributes, forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { useTheme } from '@/lib/ThemeContext';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90 dark:bg-primary/80 dark:hover:bg-primary',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90 dark:bg-destructive/80 dark:hover:bg-destructive',
        outline: 'border border-input hover:bg-accent hover:text-accent-foreground dark:border-gray-700 dark:hover:bg-gray-800',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 dark:bg-gray-700 dark:text-gray-200',
        ghost: 'hover:bg-accent hover:text-accent-foreground dark:hover:bg-gray-800',
        link: 'underline-offset-4 hover:underline text-primary dark:text-primary/90',
      },
      size: {
        default: 'h-10 py-2 px-4',
        sm: 'h-9 px-3 rounded-md',
        lg: 'h-11 px-8 rounded-md',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    const { theme } = useTheme();
    
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        data-theme={theme}
        {...props}
      />
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants };