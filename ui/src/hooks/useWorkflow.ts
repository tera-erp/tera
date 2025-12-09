/**
 * Hook: useWorkflow
 * Manage workflow state transitions for records
 */
import { useState, useCallback } from 'react';
import { WorkflowEngine, WorkflowConfig, WorkflowTransition, ActionHandler } from '@/modules';

export interface UseWorkflowState {
  currentState: string;
  stateLabel: string;
  stateColor: string;
  canEdit: boolean;
  canDelete: boolean;
  availableTransitions: Array<[string, WorkflowTransition]>;
  transition: (transitionKey: string) => Promise<boolean>;
  executeAction: (actionKey: string, actionConfig: any, data: any) => Promise<any>;
  canTransition: (transitionKey: string) => boolean;
}

export function useWorkflow(
  workflowConfig: WorkflowConfig,
  recordId?: string | number
): UseWorkflowState {
  const [engine] = useState(() => new WorkflowEngine(workflowConfig));

  const transition = useCallback(
    async (transitionKey: string): Promise<boolean> => {
      return engine.transition(transitionKey);
    },
    [engine]
  );

  const executeAction = useCallback(
    async (actionKey: string, actionConfig: any, data: any) => {
      const context = {
        recordId,
        data,
        permissions: [], // Would be populated from auth context in real implementation
      };

      return await ActionHandler.execute(actionKey, actionConfig, context);
    },
    [recordId]
  );

  const canTransition = useCallback(
    (transitionKey: string): boolean => {
      return engine.canTransition(transitionKey);
    },
    [engine]
  );

  return {
    currentState: engine.getCurrentState(),
    stateLabel: engine.getStateLabel(),
    stateColor: engine.getStateColor(),
    canEdit: engine.canEdit(),
    canDelete: engine.canDelete(),
    availableTransitions: engine.getAvailableTransitions(),
    transition,
    executeAction,
    canTransition,
  };
}
