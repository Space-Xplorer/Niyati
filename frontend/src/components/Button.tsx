import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ children, isLoading, ...props }) => {
    return (
        <button
            {...props}
            disabled={isLoading || props.disabled}
            className={`px-6 py-3 rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed ${props.className || ''}`}
            style={{
                backgroundColor: '#dbf226',
                color: '#005b52',
                border: 'none',
                fontWeight: '600',
                ...props.style
            }}
            onMouseEnter={(e) => {
                if (!isLoading && !props.disabled) {
                    e.currentTarget.style.backgroundColor = '#b8cc1f';
                }
            }}
            onMouseLeave={(e) => {
                if (!isLoading && !props.disabled) {
                    e.currentTarget.style.backgroundColor = '#dbf226';
                }
            }}
        >
            {isLoading ? (
                <span className="flex items-center justify-center space-x-2">
                    <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" style={{ color: '#005b52' }}>
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Processing...</span>
                </span>
            ) : (
                children
            )}
        </button>
    );
};
