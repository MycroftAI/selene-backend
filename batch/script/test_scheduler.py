"""Job to test the scheduler functionality.

This job is run through the batch job scheduler.  It contains assertion
statements that test the functionality of the code in the
job_scheduler.job module.
"""
from datetime import date, timedelta

from selene.batch.base import SeleneScript


class TestScheduler(SeleneScript):
    def __init__(self):
        super(TestScheduler, self).__init__(__file__)

    def _define_args(self):
        """Pass an arg with value and arg without value to the script

        The scheduler needs to be able to handle arguments that take a value
        and those that do not.  Define one of each and specify them in the
        scheduler.
        """
        super(TestScheduler, self)._define_args()
        self._arg_parser.add_argument(
            "--arg-with-value",
            help='Argument to test passing a value with an argument',
            required=True,
            type=str
        )
        self._arg_parser.add_argument(
            "--arg-no-value",
            help='Argument to test passing a value with an argument',
            action="store_true"
        )

    def _run(self):
        self.log.info('Running the scheduler test job')
        assert self.args.arg_no_value
        assert self.args.arg_with_value == 'test'

        # Tests the logic that overrides the default date in the scheduler.
        assert self.args.date == date.today() - timedelta(days=1)


if __name__ == '__main__':
    TestScheduler().run()
