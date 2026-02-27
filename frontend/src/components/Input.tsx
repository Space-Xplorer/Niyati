import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input: React.FC<InputProps> = (props) => {
  return (
    <input
      {...props}
      className={`w-full px-4 py-3 rounded-lg border transition-all ${props.className || ''}`}
      style={{
        borderColor: '#d0d0d0',
        backgroundColor: '#ffffff',
        color: '#1a1a1a',
        ...props.style
      }}
      onFocus={(e) => {
        e.currentTarget.style.borderColor = '#005b52';
        e.currentTarget.style.outline = '2px solid #dbf226';
        e.currentTarget.style.outlineOffset = '0px';
      }}
      onBlur={(e) => {
        e.currentTarget.style.borderColor = '#d0d0d0';
        e.currentTarget.style.outline = 'none';
      }}
    />
  );
};
