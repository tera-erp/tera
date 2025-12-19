import { useState, useEffect } from 'react';

interface BackendHealth {
  isHealthy: boolean;
  isLoading: boolean;
  error: string | null;
  modulesLoaded: number;
}

export function useBackendHealth() {
  const [health, setHealth] = useState<BackendHealth>({
    isHealthy: false,
    isLoading: true,
    error: null,
    modulesLoaded: 0,
  });

  useEffect(() => {
    let mounted = true;
    let retryCount = 0;
    const maxRetries = 10;
    const retryDelay = 2000; // 2 seconds

    const checkHealth = async () => {
      try {
        const response = await fetch('/api/v1/health');
        
        if (!response.ok) {
          throw new Error(`Health check failed: ${response.status}`);
        }

        const data = await response.json();
        
        if (mounted) {
          setHealth({
            isHealthy: data.status === 'healthy',
            isLoading: false,
            error: null,
            modulesLoaded: data.modules_loaded || 0,
          });
        }
      } catch (error) {
        console.error('Backend health check failed:', error);
        
        if (retryCount < maxRetries) {
          retryCount++;
          if (mounted) {
            setHealth(prev => ({
              ...prev,
              isLoading: true,
              error: `Tera is starting up... (${retryCount}/${maxRetries})`,
            }));
          }
          setTimeout(checkHealth, retryDelay);
        } else {
          if (mounted) {
            setHealth({
              isHealthy: false,
              isLoading: false,
              error: 'System is not responding.',
              modulesLoaded: 0,
            });
          }
        }
      }
    };

    checkHealth();

    return () => {
      mounted = false;
    };
  }, []);

  return health;
}
