
if __name__ == "__main__":
    from levelapp.workflow.schemas import WorkflowConfig
    from levelapp.core.session import EvaluationSession

    # Load configuration from YAML
    config = WorkflowConfig.load(path="../data/workflow_config.yaml")

    # Run evaluation session
    with EvaluationSession(session_name="sim-test", workflow_config=config) as session:
        session.run()
        results = session.workflow.collect_results()
        print("Results:", results)

    stats = session.get_stats()
    print(f"session stats:\n{stats}")
