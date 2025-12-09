/**
 * Module Configuration Types
 * Auto-generated from backend YAML schema
 */

export type FieldType = 
  | 'text'
  | 'email'
  | 'number'
  | 'decimal'
  | 'date'
  | 'datetime'
  | 'select'
  | 'checkbox'
  | 'textarea'
  | 'array'
  | 'richtext'
  | 'file'
  | 'rating'
  | 'tags';

export type FieldSize = 'full' | 'half' | 'third' | 'two-thirds';

export interface FormFieldConfig {
  type: FieldType;
  label: string;
  required?: boolean;
  readonly?: boolean;
  disabled?: boolean;
  help_text?: string;
  placeholder?: string;
  default?: any;
  
  // UI Layout
  size?: FieldSize;
  grid_column?: number;
  hidden?: boolean;
  hidden_if?: string;  // JS expression
  disabled_if?: string;  // JS expression
  
  // For select/dropdown
  endpoint?: string;
  display_field?: string;
  value_field?: string;
  searchable?: boolean;
  clearable?: boolean;
  options?: Array<{
    value: string;
    label: string;
  }>;
  
  // For arrays
  fields?: Record<string, FormFieldConfig>;
  min_rows?: number;
  max_rows?: number;
  
  // Computed fields
  formula?: string;
  
  // Validation
  pattern?: string;
  min?: number | string;
  max?: number | string;
  minLength?: number;
  maxLength?: number;
}

export type FormLayoutType = 'grid' | 'tabs' | 'accordion' | 'wizard';

export interface FormLayout {
  type: FormLayoutType;
  columns?: number;
  gaps?: 'small' | 'medium' | 'large';
  sections?: {
    title?: string;
    description?: string;
    fields: string[];
    icon?: string;
  }[];
}

export interface BackButtonConfig {
  enabled?: boolean;
  label?: string;
  navigate_to?: string;
}

export interface FormConfig {
  title: string;
  description?: string;
  edit_title?: string;
  edit_description?: string;
  fields: Record<string, FormFieldConfig>;
  layout?: FormLayout;
  submit_label?: string;
  edit_submit_label?: string;
  cancel_label?: string;
  back_button?: BackButtonConfig;
}

export interface ScreenConfig {
  title: string;
  description?: string;
  path: string;
  type: 'list' | 'detail' | 'form' | 'dashboard' | 'custom';
  
  // Navigation
  show_in_nav?: boolean;
  create_screen?: string;  // Screen ID to navigate to for creation (for list screens)
  
  // Data source
  endpoint?: string;
  list_endpoint?: string;
  detail_endpoint?: string;
  
  // Permissions
  permissions?: string[];
  
  // List view config
  list_config?: {
    columns: string[];  // Field keys to display
    searchable_fields?: string[];
    sortable?: boolean;
    filterable?: boolean;
    paginated?: boolean;
    page_size?: number;
    selectable?: boolean;
    row_actions?: Array<{
      id: string;
      label: string;
      icon?: string;
      action: string;  // Action key
      color?: string;
      confirm?: boolean;
    }>;
  };
  
  // Detail view config
  detail_config?: {
    form?: string;  // Form key
    show_metadata?: boolean;
    show_related?: boolean;
    sidebar?: {
      show_metadata?: boolean;
      show_related?: boolean;
      widgets?: string[];
    };
    actions?: string[];  // Action keys
    related_records?: Array<{
      label: string;
      endpoint: string;
      display_field: string;
    }>;
  };
  
  // Responsive
  layout?: 'full' | 'sidebar' | 'two-column';
  mobile_hidden?: boolean;
}

export interface WorkflowState {
  label: string;
  color?: string;
  can_transition_to: string[];
  allow_edit: boolean;
  allow_delete: boolean;
}

export interface WorkflowTransition {
  from: string;
  to: string;
  label: string;
  action: string;
  confirm_message?: string;
  disabled_if?: string;
  permissions?: string[];
}

export interface WorkflowConfig {
  title: string;
  initial_state: string;
  states: Record<string, WorkflowState>;
  transitions?: Record<string, WorkflowTransition>;
}

export interface ActionConfig {
  type: 'api' | 'custom' | 'batch';
  method?: string;
  endpoint?: string;
  handler?: string;
  success_message?: string;
  error_message?: string;
  on_success?: Array<Record<string, any>>;
}

export interface MenuItemConfig {
  title: string;
  path: string;
  icon?: string;
  permission?: string;
}

export interface ModuleConfig {
  module: {
    id: string;
    name: string;
    version: string;
    description?: string;
    author?: string;
    icon?: string;  // Lucide icon name
    color?: string;  // Color class/css var
  };
  screens?: Record<string, ScreenConfig>;
  forms?: Record<string, FormConfig>;
  workflows?: Record<string, WorkflowConfig>;
  actions?: Record<string, ActionConfig>;
  permissions?: string[];
  menu?: Array<{
    id: string;
    title: string;
    icon?: string;
    path?: string;
    items?: MenuItemConfig[];
  }>;
}

/**
 * Module metadata for runtime
 */
export interface ModuleMetadata {
  id: string;
  name: string;
  version: string;
  config: ModuleConfig;
}
