/**
 * Form Field Utilities
 * Helper functions for determining field editability based on workflows and conditions
 */
import { FormFieldConfig, WorkflowConfig } from './types';

export class FormFieldUtils {
  /**
   * Check if a field can be edited in a given workflow state
   */
  static canEditField(
    field: FormFieldConfig,
    workflowState?: string,
    workflowConfig?: WorkflowConfig
  ): boolean {
    // If field is marked as readonly/disabled, it cannot be edited
    if (field.readonly || field.disabled) {
      return false;
    }

    // If no workflow state, field is editable by default
    if (!workflowState || !workflowConfig) {
      return true;
    }

    // Check if workflow state allows editing
    const stateConfig = workflowConfig.states[workflowState];
    if (!stateConfig?.allow_edit) {
      return false;
    }

    // Check for state-specific disabled_if conditions
    if (field.disabled_if) {
      // Simple check: if the field has disabled_if and it mentions the current state
      // For example, disabled_if: "status === 'completed'"
      if (field.disabled_if.includes(workflowState)) {
        return false;
      }
    }

    return true;
  }

  /**
   * Get effective readonly status for a field
   */
  static isFieldReadonly(
    field: FormFieldConfig,
    workflowState?: string,
    workflowConfig?: WorkflowConfig
  ): boolean {
    return !this.canEditField(field, workflowState, workflowConfig);
  }

  /**
   * Filter form fields that are editable in a given workflow state
   */
  static getEditableFields(
    fields: Record<string, FormFieldConfig>,
    workflowState?: string,
    workflowConfig?: WorkflowConfig
  ): Record<string, FormFieldConfig> {
    if (!workflowState || !workflowConfig) {
      return fields;
    }

    const editable: Record<string, FormFieldConfig> = {};

    for (const [key, field] of Object.entries(fields)) {
      if (this.canEditField(field, workflowState, workflowConfig)) {
        editable[key] = field;
      }
    }

    return editable;
  }

  /**
   * Get display message about field availability
   */
  static getFieldStatusMessage(
    field: FormFieldConfig,
    workflowState?: string,
    workflowConfig?: WorkflowConfig
  ): string | null {
    if (!workflowState || !workflowConfig) {
      return null;
    }

    const stateConfig = workflowConfig.states[workflowState];
    if (!stateConfig?.allow_edit) {
      return `Cannot edit fields in ${workflowState} state`;
    }

    return null;
  }
}
