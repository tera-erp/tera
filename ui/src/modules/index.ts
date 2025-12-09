/**
 * Module index - Exports all module system components
 */

export { ModuleFactory } from './ModuleFactory';
export { WorkflowEngine } from './WorkflowEngine';
export { ActionHandler, type ActionResult } from './ActionHandler';
export { FormRenderer, ListRenderer, DetailRenderer } from './components';
export type {
  FieldType,
  FormFieldConfig,
  FormConfig,
  FormLayout,
  ScreenConfig,
  WorkflowState,
  WorkflowTransition,
  WorkflowConfig,
  ActionConfig,
  MenuItemConfig,
  ModuleConfig,
  ModuleMetadata,
} from './types';

