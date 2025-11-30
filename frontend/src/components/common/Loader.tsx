import { FC } from 'react';

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export const Loader: FC<LoaderProps> = ({ size = 'md', text }) => {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`${sizeClasses[size]} animate-spin rounded-full border-4 border-gray-200 border-t-primary-600`}></div>
      {text && <p className="mt-4 text-gray-600">{text}</p>}
    </div>
  );
};

