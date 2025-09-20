import { expect } from "chai";
import { sortArrayByOrder } from "../../src/js/shared/array";

describe("Array sort", () => {
    it("should sort order according to given order", () => {
        const arr = ["3s", "3p", "3d", "4s"];
        const ord = [
            "1s",
            "2s",
            "2p",
            "3s",
            "3p",
            "4s",
            "3d",
            "4p",
            "5s",
            "4d",
            "5p",
            "6s",
            "4f",
            "5d",
            "6p",
            "7s",
            "5f",
            "6d",
            "7p",
            "8s",
        ];
        const result = sortArrayByOrder(arr, ord);
        expect(result).to.deep.equal(["3s", "3p", "4s", "3d"]);
    });
});
