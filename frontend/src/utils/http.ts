import { AxiosError } from 'axios';

export const getErrorMessage = (error: unknown): string => {
  if (error instanceof AxiosError) {
    return error.response?.data?.detail || error.message || 'An error occurred';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
};

export const handleApiError = (error: unknown): never => {
  const message = getErrorMessage(error);
  throw new Error(message);
};

