import { forwardRef, type ButtonHTMLAttributes } from 'react';

// Define the props for our button
export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
  size?: 'default' | 'sm' | 'lg'; // NEW: Add a size prop
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, children, isLoading = false, size = 'default', ...props }, ref) => {
    
    // Define size classes
    const sizeClasses = {
      default: 'px-6 py-3 text-base',
      sm: 'px-4 py-2 text-sm',
      lg: 'px-8 py-4 text-lg'
    };
    
    return (
      <button
        className={`relative inline-flex items-center justify-center rounded-xl font-bold transition-all duration-300 transform hover:scale-[1.02] active:scale-95 disabled:cursor-not-allowed disabled:scale-100 disabled:bg-slate-500 group ${sizeClasses[size]} ${className}`}
        disabled={isLoading}
        ref={ref}
        {...props}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Loading...
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);
Button.displayName = "Button";

