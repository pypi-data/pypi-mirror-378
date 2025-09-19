from tabpfn_common_utils.telemetry.core.service import ProductTelemetry


if __name__ == "__main__":
    x = ProductTelemetry().telemetry_enabled()
    print(x)
