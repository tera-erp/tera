/**
 * Action Handler - Executes workflow actions
 */
import { ActionConfig } from './types';

export interface ActionResult {
  success: boolean;
  message: string;
  data?: any;
  redirect_to?: string;
}

export class ActionHandler {
  /**
   * Execute an action
   */
  static async execute(
    actionKey: string,
    actionConfig: ActionConfig,
    context: {
      recordId?: string | number;
      data: Record<string, any>;
      permissions: string[];
    }
  ): Promise<ActionResult> {
    try {
      if (actionConfig.type === 'api') {
        return await this.executeApiAction(actionConfig, context);
      } else if (actionConfig.type === 'custom') {
        return await this.executeCustomAction(actionKey, actionConfig, context);
      } else if (actionConfig.type === 'batch') {
        return await this.executeBatchAction(actionConfig, context);
      }

      return {
        success: false,
        message: `Unknown action type: ${actionConfig.type}`,
      };
    } catch (error) {
      return {
        success: false,
        message: actionConfig.error_message || `Action failed: ${error}`,
      };
    }
  }

  /**
   * Execute API action
   */
  private static async executeApiAction(
    config: ActionConfig,
    context: {
      recordId?: string | number;
      data: Record<string, any>;
      permissions: string[];
    }
  ): Promise<ActionResult> {
    if (!config.endpoint || !config.method) {
      return {
        success: false,
        message: 'API action missing endpoint or method',
      };
    }

    // Replace path parameters
    let endpoint = config.endpoint;
    if (context.recordId) {
      endpoint = endpoint.replace('{id}', String(context.recordId));
    }

    const options: RequestInit = {
      method: config.method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (config.method !== 'GET') {
      options.body = JSON.stringify(context.data);
    }

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
      };
    }

    const response = await fetch(endpoint, options);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        message:
          config.error_message ||
          errorData.detail ||
          `Request failed with status ${response.status}`,
      };
    }

    const responseData = await response.json().catch(() => ({}));

    return {
      success: true,
      message: config.success_message || 'Action completed successfully',
      data: responseData,
      redirect_to: this.resolveRedirect(config.on_success),
    };
  }

  /**
   * Execute custom action (client-side only)
   */
  private static async executeCustomAction(
    actionKey: string,
    config: ActionConfig,
    context: any
  ): Promise<ActionResult> {
    // Custom handlers would be registered by modules
    // This is a placeholder for custom logic
    return {
      success: true,
      message: config.success_message || 'Action completed',
    };
  }

  /**
   * Execute batch action
   */
  private static async executeBatchAction(
    config: ActionConfig,
    context: any
  ): Promise<ActionResult> {
    // Handle batch operations (multiple records)
    return {
      success: true,
      message: config.success_message || 'Batch action completed',
    };
  }

  /**
   * Resolve redirect target from on_success actions
   */
  private static resolveRedirect(onSuccess?: Array<Record<string, any>>): string | undefined {
    if (!onSuccess) return undefined;

    for (const action of onSuccess) {
      if ('navigate_to' in action) {
        return action.navigate_to;
      }
    }

    return undefined;
  }
}
