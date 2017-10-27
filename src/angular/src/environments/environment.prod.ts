import {LoggerService} from "../app/common/logger.service"

export const environment = {
    production: true,
    logger: {
        level: LoggerService.Level.WARN
    }
};
