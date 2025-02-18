# AI Agent Task Prompt: Algorand Node Implementation on Hetzner Server

## OBJECTIVE
Create and execute a detailed implementation plan for setting up an Algorand node on a Hetzner server, following the specifications and validation steps outlined in the project requirements document.

## CONTEXT
You are operating on:
- Hetzner Dedicated Server AX52
- Location: Germany, FSN1
- OS: Ubuntu 22.04.2 LTS (English)
- Primary IPv4 Address provided

## TASK SEQUENCE

1. INITIALIZATION
- Create directory: `mkdir -p ProjectRequirements`
- Navigate to directory: `cd ProjectRequirements`
- Initialize implementation plan: Create `algorand_node_implementation_plan.md`

2. PRE-IMPLEMENTATION VALIDATION
Execute each check in the Pre-Implementation Checklist:
- Run all resource validation commands
- Document results in a structured format
- Halt and report if any check fails

3. PHASED IMPLEMENTATION
Execute each phase sequentially, with mandatory validation steps:

FOR EACH PHASE:
- Execute commands as specified
- Run validation commands after each step
- Store command outputs
- Compare outputs against expected results
- Proceed only if validation passes
- If validation fails, execute rollback procedure

4. MONITORING SETUP
- Install and configure monitoring tools
- Verify monitoring system functionality
- Test alert configurations

5. HEALTH CHECK IMPLEMENTATION
- Deploy automated health check scripts
- Verify script execution
- Test alert mechanisms

## SUCCESS CRITERIA VALIDATION
After implementation, verify against Success Criteria Matrix:

FOR EACH CRITERION:
- Execute check command
- Compare result with expected output
- Document compliance status
- Flag any deviations

## ERROR HANDLING
IF any step fails:
1. Capture error output
2. Document current state
3. Execute relevant rollback procedure
4. Report failure with context
5. Await human intervention

## REPORTING REQUIREMENTS
Generate implementation report including:
1. Pre-implementation check results
2. Phase-by-phase execution logs
3. Validation step results
4. Final success criteria compliance
5. Any errors encountered and resolutions
6. Current system state

## CONSTRAINTS
- Must follow sequence exactly as specified
- Must validate each step before proceeding
- Must maintain detailed logs
- Must not proceed past failed validations
- Must execute rollback procedures on failures

## COMPLETION CRITERIA
Implementation is considered complete when:
1. All phases are successfully executed
2. All validation steps pass
3. Success criteria matrix is fully satisfied
4. Monitoring systems are operational
5. Health checks are running
6. Implementation report is generated

## DELIVERABLES
1. Completed implementation plan
2. Implementation execution logs
3. Validation results
4. Monitoring system configuration
5. Health check scripts
6. Final implementation report

## SAFETY MEASURES
- Maintain backup at each phase
- Verify rollback procedures
- Test recovery processes
- Document all changes
- Preserve original configurations

Report any unexpected behavior or deviations from the plan immediately. 