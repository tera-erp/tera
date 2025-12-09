/**
 * Module Path Debugger
 * Utility for debugging module path matching issues
 */

interface ScreenPathInfo {
  key: string;
  path: string;
  type: string;
  pattern: string;
  matches: boolean;
}

export class ModulePathDebugger {
  /**
   * Debug path matching for a module
   */
  static debugPathMatching(
    currentPath: string,
    screens: Record<string, any>
  ): ScreenPathInfo[] {
    return Object.entries(screens || {}).map(([key, screen]) => {
      const screenPath = screen?.path;
      const pattern = this.buildPattern(screenPath);
      const regex = new RegExp(pattern);
      const matches = regex.test(currentPath);

      return {
        key,
        path: screenPath,
        type: screen?.type,
        pattern,
        matches,
      };
    });
  }

  /**
   * Build regex pattern from screen path
   */
  static buildPattern(screenPath: string): string {
    if (!screenPath) return "";

    const normalized = screenPath.replace(/\/$/, "");
    const escaped = normalized
      .replace(/[-/\\^$+?.()|[\]{}]/g, "\\$&")
      .replace(/\\\{id\\\}/g, "([^/]+)");

    return `^${escaped}$`;
  }

  /**
   * Get detailed debug info for a module path issue
   */
  static getDebugInfo(
    currentPath: string,
    moduleId: string,
    screens: Record<string, any>
  ): string {
    const debugInfo = this.debugPathMatching(currentPath, screens);
    const matches = debugInfo.filter((d) => d.matches);

    let output = `\n═══════════════════════════════════════\n`;
    output += `Module Path Debug Info\n`;
    output += `═══════════════════════════════════════\n`;
    output += `Current Path: ${currentPath}\n`;
    output += `Module ID: ${moduleId}\n`;
    output += `Total Screens: ${debugInfo.length}\n`;
    output += `Matching Screens: ${matches.length}\n\n`;

    if (matches.length > 0) {
      output += `✓ MATCHED SCREENS:\n`;
      matches.forEach((m) => {
        output += `  - ${m.key} (${m.type})\n`;
        output += `    Path: ${m.path}\n`;
      });
    } else {
      output += `✗ NO MATCHING SCREENS\n\n`;
      output += `Available Screens:\n`;
      debugInfo.forEach((d) => {
        output += `  ✗ ${d.key} (${d.type})\n`;
        output += `    Path: ${d.path}\n`;
        output += `    Pattern: ${d.pattern}\n`;
      });
    }

    output += `═══════════════════════════════════════\n`;
    return output;
  }

  /**
   * Validate module config structure
   */
  static validateModuleConfig(config: any): string[] {
    const errors: string[] = [];

    if (!config.module?.id) {
      errors.push("Missing module.id");
    }

    if (!config.screens || Object.keys(config.screens).length === 0) {
      errors.push("No screens defined");
    }

    Object.entries(config.screens || {}).forEach(([key, screen]: any) => {
      if (!screen.path) {
        errors.push(`Screen '${key}' missing path`);
      }
      if (!screen.type) {
        errors.push(`Screen '${key}' missing type`);
      }
      if (screen.type === "detail" && !screen.endpoint) {
        errors.push(`Detail screen '${key}' missing endpoint`);
      }
    });

    return errors;
  }
}

/**
 * Log module path matching for debugging
 */
export function logModuleDebug(
  currentPath: string,
  moduleId: string,
  screens: Record<string, any>
) {
  if (process.env.NODE_ENV !== "development") return;

  const debugInfo = ModulePathDebugger.getDebugInfo(
    currentPath,
    moduleId,
    screens
  );
  console.log(debugInfo);
}
