/**
 * Module Factory - Loads and instantiates modules at runtime
 */
import { ModuleConfig, ModuleMetadata, ScreenConfig } from './types';
import { lazy, ComponentType, ReactNode } from 'react';

export class ModuleFactory {
  private static modules: Map<string, ModuleMetadata> = new Map();
  private static configs: Map<string, ModuleConfig> = new Map();

  /**
   * Fetch all module configs from backend
   */
  static async loadModules(): Promise<ModuleConfig[]> {
    try {
      const response = await fetch('/api/v1/modules', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch modules');
      }

      const modules = await response.json();
      
      // Cache configs
      modules.forEach((config: ModuleConfig) => {
        this.configs.set(config.module.id, config);
      });

      return modules;
    } catch (error) {
      console.error('Failed to load modules:', error);
      return [];
    }
  }

  /**
   * Register a module
   */
  static registerModule(
    moduleId: string,
    config: ModuleConfig,
    components: Record<string, ComponentType<any>>
  ): void {
    this.configs.set(moduleId, config);
    this.modules.set(moduleId, {
      id: moduleId,
      name: config.module.name,
      version: config.module.version,
      config,
      components,
    });
  }

  /**
   * Get a registered module
   */
  static getModule(moduleId: string): ModuleMetadata | undefined {
    return this.modules.get(moduleId);
  }

  /**
   * Get module config
   */
  static getConfig(moduleId: string): ModuleConfig | undefined {
    return this.configs.get(moduleId);
  }

  /**
   * Get all registered modules
   */
  static getAllModules(): ModuleMetadata[] {
    return Array.from(this.modules.values());
  }

  /**
   * Get screen configuration
   */
  static getScreen(
    moduleId: string,
    screenId: string
  ): ScreenConfig | undefined {
    const config = this.configs.get(moduleId);
    return config?.screens?.[screenId];
  }

  /**
   * Get all menu items for a module
   */
  static getMenuItems(moduleId: string) {
    const config = this.configs.get(moduleId);
    return config?.menu || [];
  }

  /**
   * Check if user has permission for a resource
   */
  static hasPermission(
    moduleId: string,
    screenId: string,
    userPermissions: string[]
  ): boolean {
    const screen = this.getScreen(moduleId, screenId);
    if (!screen?.permissions || screen.permissions.length === 0) {
      return true; // No permissions required
    }

    return screen.permissions.some((p) => userPermissions.includes(p));
  }

  /**
   * Dynamically load a screen component
   */
  static loadScreenComponent(
    moduleId: string,
    screenId: string
  ): ComponentType<any> | null {
    const module = this.modules.get(moduleId);
    const screen = this.getScreen(moduleId, screenId);

    if (!module || !screen) {
      return null;
    }

    return module.components[screen.component] || null;
  }

  /**
   * Get all screens for a module
   */
  static getScreens(moduleId: string): Array<[string, ScreenConfig]> {
    const config = this.configs.get(moduleId);
    return Object.entries(config?.screens || {});
  }

  /**
   * Get all routes for all modules
   */
  static generateRoutes(): Array<{
    path: string;
    component: ComponentType<any>;
    moduleId: string;
    screenId: string;
    permissions?: string[];
  }> {
    const routes = [];

    for (const [moduleId, config] of this.configs.entries()) {
      const module = this.modules.get(moduleId);
      if (!module) continue;

      for (const [screenId, screen] of Object.entries(
        config.screens || {}
      )) {
        const component = module.components[screen.component];
        if (component) {
          routes.push({
            path: screen.path,
            component,
            moduleId,
            screenId,
            permissions: screen.permissions,
          });
        }
      }
    }

    return routes;
  }
}
