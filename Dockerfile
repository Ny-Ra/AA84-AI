FROM public.ecr.aws/lambda/python:3.13

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

COPY app/ ${LAMBDA_TASK_ROOT}/app/

# Default to Lambda handler, can be overridden for local dev
CMD ["app.main.handler"]