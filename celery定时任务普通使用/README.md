# 备注

**启动定时任务**

	#任务调度器 celery beat
	celery -A periodic_task beat

	#启动worker
	celery -A periodic_task worker -l debug