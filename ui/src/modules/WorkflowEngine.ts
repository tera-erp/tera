/**
 * Workflow Engine - Client-side state machine
 */
import { WorkflowConfig, WorkflowTransition } from './types';

export class WorkflowEngine {
  private config: WorkflowConfig;
  private currentState: string;
  private stateHistory: string[] = [];

  constructor(config: WorkflowConfig) {
    this.config = config;
    this.currentState = config.initial_state;
    this.stateHistory.push(this.currentState);
  }

  /**
   * Get current workflow state
   */
  getCurrentState(): string {
    return this.currentState;
  }

  /**
   * Check if a transition is allowed from current state
   */
  canTransition(transitionKey: string): boolean {
    const transition = this.config.transitions?.[transitionKey];
    if (!transition) return false;

    return transition.from === this.currentState;
  }

  /**
   * Get available transitions from current state
   */
  getAvailableTransitions(): Array<[string, WorkflowTransition]> {
    const transitions = this.config.transitions || {};
    return Object.entries(transitions).filter(
      ([_, t]) => t.from === this.currentState
    );
  }

  /**
   * Perform a state transition
   */
  transition(transitionKey: string): boolean {
    const transition = this.config.transitions?.[transitionKey];
    if (!transition || !this.canTransition(transitionKey)) {
      return false;
    }

    const nextState = transition.to;
    this.currentState = nextState;
    this.stateHistory.push(nextState);
    return true;
  }

  /**
   * Check if editing is allowed in current state
   */
  canEdit(): boolean {
    return this.config.states[this.currentState]?.allow_edit ?? false;
  }

  /**
   * Check if deletion is allowed in current state
   */
  canDelete(): boolean {
    return this.config.states[this.currentState]?.allow_delete ?? false;
  }

  /**
   * Get state label
   */
  getStateLabel(): string {
    return this.config.states[this.currentState]?.label ?? this.currentState;
  }

  /**
   * Get state color
   */
  getStateColor(): string {
    return this.config.states[this.currentState]?.color ?? 'gray';
  }

  /**
   * Get state history
   */
  getHistory(): string[] {
    return [...this.stateHistory];
  }

  /**
   * Reset to initial state
   */
  reset(): void {
    this.currentState = this.config.initial_state;
    this.stateHistory = [this.currentState];
  }
}
