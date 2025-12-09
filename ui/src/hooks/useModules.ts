/**
 * Hook: useModules
 * Load and manage modules from the backend API
 */
import { useEffect, useState } from 'react';
import { ModuleFactory, ModuleConfig } from '@/modules';

export interface UseModulesState {
  modules: ModuleConfig[];
  loading: boolean;
  error: string | null;
  getModule: (moduleId: string) => ModuleConfig | undefined;
  hasPermission: (moduleId: string, screenId: string, userPermissions: string[]) => boolean;
}

export function useModules(): UseModulesState {
  const [modules, setModules] = useState<ModuleConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadModules = async () => {
      try {
        setLoading(true);
        const loadedModules = await ModuleFactory.loadModules();
        setModules(loadedModules);
        setError(null);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to load modules';
        setError(errorMsg);
        console.error('Failed to load modules:', err);
      } finally {
        setLoading(false);
      }
    };

    loadModules();
  }, []);

  const getModule = (moduleId: string): ModuleConfig | undefined => {
    return ModuleFactory.getConfig(moduleId);
  };

  const hasPermission = (
    moduleId: string,
    screenId: string,
    userPermissions: string[]
  ): boolean => {
    return ModuleFactory.hasPermission(moduleId, screenId, userPermissions);
  };

  return {
    modules,
    loading,
    error,
    getModule,
    hasPermission,
  };
}
