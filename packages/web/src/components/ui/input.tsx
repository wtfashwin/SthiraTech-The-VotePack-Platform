import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={`w-full px-4 py-3 bg-white border-2 border-gray-200 rounded-xl transition-all duration-300 outline-none text-gray-900 placeholder-gray-400 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 ${className}`}
        ref={ref}
        {...props}
      />
    );
  }
);
