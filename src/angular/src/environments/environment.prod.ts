import {LoggerService} from "../app/logger.service"

export const environment = {
    production: true,
    logger: {
        level: LoggerService.Level.WARN
    }
};
